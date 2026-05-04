import requests
import subprocess

cookies = {
    'Hm_lvt_f80b2b389f44bbfb3bfe1704817d44e0': '1777305753,1777360136,1777444863,1777618117',
    'HMACCOUNT': 'C26110A792EB87EE',
    'sessionid': 'adwmojjyqb595vwtkuyg4wfxeggpsdc4',
    'Hm_lpvt_f80b2b389f44bbfb3bfe1704817d44e0': '1777618143',
}

headers = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Pragma': 'no-cache',
    'Referer': 'https://match.yuanrenxue.cn/match/2',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0',
    'X-Requested-With': 'XMLHttpRequest',
    'sec-ch-ua': '"Microsoft Edge";v="147", "Not.A/Brand";v="8", "Chromium";v="147"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}

# Node.js 脚本：执行混淆JS，Hook document.cookie 提取 m 值
NODE_SCRIPT = '''
var _console = console;
var _require = require;

var navigator = { userAgent: 'Mozilla/5.0' };
var location = { href: 'https://match.yuanrenxue.cn/match/2' };

var cookieStr = '';
var document = {
    set cookie(val) { cookieStr = val; },
    get cookie() { return cookieStr; }
};

var setTimeout = function(fn, ms) { return 0; };
var setInterval = function(fn, ms) { return 0; };
var screen = { width: 1920, height: 1080 };
var history = {};

try {
    var code = _require('fs').readFileSync('q2.js', 'utf8');
    eval(code);
    
    var match = document.cookie.match(/m=([^;]+)/);
    if (match) {
        _console.log(match[1]);
    } else {
        var match2 = document.cookie.match(/mundefined=([^;]+)/);
        if (match2) {
            _console.log(match2[1]);
        }
    }
} catch(e) {
    _console.error('Error:', e.message);
}
'''
def get_m_value(js_code):
    """执行混淆JS，提取m值"""
    with open('q2.js', 'w', encoding='utf-8') as f:
        f.write(js_code)
    with open('run_q2.js', 'w', encoding='utf-8') as f:
        f.write(NODE_SCRIPT)
    
    result = subprocess.run(
        ['node', 'run_q2.js'],
        capture_output=True, text=True, encoding='utf-8'
    )
    output = result.stdout.strip()
    if output and '|' in output:
        return output
    raise ValueError(f"无法提取m值，输出: {output}")


total = 0
for page in range(1, 6):
    if page == 5:
        headers['User-Agent'] = 'yuanrenxue'
    
    url = f'https://match.yuanrenxue.cn/api/question/2?page={page}&pageSize=10&kw='
    
    # 第一步：请求获取数据
    response = requests.get(url, cookies=cookies, headers=headers)
    result = response.json()
    
    # 如果直接返回了数据（cookie还在），就不用再执行JS了
    if isinstance(result.get('data'), list):
        data = result['data']
    else:
        # 返回的是混淆JS代码，需要执行提取m值
        js_code = result['data']
        m_value = get_m_value(js_code)
        
        # 带上m值cookie，重新请求获取真实数据
        cookies['m'] = m_value
        response2 = requests.get(url, cookies=cookies, headers=headers)
        data = response2.json().get("data", [])
    
    page_sum = sum(data)
    total += page_sum
    print(f"第{page}页的值为{page_sum}, 目前总值为{total}")

print(f"总和为{total}")
