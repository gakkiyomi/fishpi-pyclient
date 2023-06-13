import re
HOST = 'https://fishpi.cn'
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'

HELP = '输入#help获得命令提示列表'

COMMAND_GUIDE = '''
[#cli] 进入命令交互模式
[#chatroom] 进入聊天室模式
[#rp] 1128 1个128积分 (默认5个,128积分)拼手气红包
[#rp-ave] 1128 1个128积分 (默认5个,32积分)平均红包
[#rp-hb] 5128 5个128积分 (默认5个,32积分)心跳红包
[#rp-rps] 0128 128积分 (0=石头 1=剪刀 2=布)猜拳红包
[#rp-rps-limit] 100 (猜拳红包超过100的不抢)
[#rp-to] 32 Gakkiyomi,xiaoIce (积分 用户)专属红包
[#rp-time] 3 设置抢红包等待时间
[#bm] 发送清风明月
[#api-key] 打印apikey
[#answer] 进入|退出 答题模式
[#checked] 查看当前是否签到
[#reward] 领取昨日活跃奖励
[#transfer] 32 Gakkiyomi 送给你 (积分 用户 留言)
[#point] 查看当前个人积分
[#online-users] 查看当前在线的用户列表
[#user username] 输入 #user 用户名 可查看此用户详细信息 (#user Gakkiyomi)
[#blacklist] 查看黑名单列表
[#ban username] 将某人送入黑名单
[#unban username] 将某人解除黑名单
[#liveness] 查看当前活跃度(⚠️慎用，如果频繁请求此命令(最少间隔30s)，登录状态会被直接注销,需要重启脚本！)
'''

RPS_SUCCESS = '![](https://file.fishpi.cn/2023/01/XN3Y9-cf3997b7.jpeg)'
RPS_LOSED = '![](https://pwl.stackoverflow.wiki/2022/04/MB2SCYFZFVT2DQ0GI7-c6447c10.jpg)'
RPS_ZERO = '![](https://file.fishpi.cn/2023/05/1683183148506-4c31497e.png)'



RP_CODE_RE = re.compile('#rp\s{1,1}(\d)(\d+)')
RP_AVER_CODE_RE = re.compile('#rp-ave\s{1,1}(\d)(\d+)')
RP_HB_CODE_RE = re.compile('#rp-hb\s{1,1}(\d)(\d+)')
RP_RPS_CODE_RE = re.compile('#rp-rps\s{1,1}(\d)(\d+)')
RP_SEND_TO_CODE_RE = re.compile('#rp-to (\d+) ([\w,]+)(?<!,)$')
RP_TIME_CODE_RE = re.compile('#rp-time (\d+)')
TRANSFER_RE = re.compile('#transfer (\d+) (\w+)( \S+)?')