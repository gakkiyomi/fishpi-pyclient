  ![摸鱼派cn.png](https://b3logfile.com/file/2023/05/摸鱼派-cn-owZQT8f.png)

# fishpi-pyclient

> 摸鱼派聊天室 python 命令行客户端

基于摸鱼打工人社区——摸鱼派开放 API 开发的摸鱼派聊天室 python 客户端程序，可以在里面边写 Bug 边愉快地吹水摸鱼。

## 安装

### MacOS系统

[v2.0.0下载](https://github.com/gakkiyomi/fishpi-pyclient/releases/download/v2.0.0/fishpi-pyclient)

执行如下命令

1. ```bash
   chmod a+x ./fishpi-pyclient
   ```

2. ```bash
   ./fishpi-pyclient
   ```

然后需要在偏好设置这里,如下图:
![WechatIMG482.jpg](https://file.fishpi.cn/2023/12/WechatIMG482-3c599a0e.jpg)

### pip安装

环境: Python3.9 以上

执行

```bash
pip install fishpi-pyclient
```

```bash
fishpi-pyclient -u username -p password -c <两步验证码>
```

## 调试

```bash
python core.py
```

## 功能

- 🥷 账号多开
  - 一键切换
  - 更多功能请期待
- 💬 聊天模式
  - 💬 聊天吹水
  - 🤖️ 自动复读
  - 🤖️ 自动领取昨日奖励
  - 🌛 发送清风明月
  - 聊天室消息撤回
  - 🧠 自言自语
    - 自定义语句池
    - 定时发送
- 命令模式
  - 命令/聊天模式切换
    - (聊天模式也可以执行命令)
  - 进入答题模式(前缀自动加上 鸽)
  - ⬆️ 社区快捷命令
    - 领取昨日活跃度奖励
    - 查看个人积分
    - 查看签到状态
    - 转账
    - 发送清风明月
    - 查看当前活跃度
    - 查看在线用户列表
    - 查询用户详细信息
    - 🈲️ 小黑屋功能
      - 拒绝接收黑名单在聊天室发送的信息 (红包除外 😂 )
      - 将某人从小黑屋中放出
    - 🈲️ 关键字屏蔽  
    - 发红包🧧
      - 拼手气红包
      - 普通红包
      - 专属红包
      - 心跳红包
      - 猜拳红包
      - 设置抢红包等待时间
      - 抢猜拳红包最大限制
      - 🧧 自动化抢红包（脚本哥）
        - 自定义抢红包延时
        - 心跳红包防止踩坑
        - 心跳红包风险预测

## 效果

![fenshen.png](https://file.fishpi.cn/2023/12/账号分身-0a25be81.png)
![image.png](https://file.fishpi.cn/2023/06/image-d4da9bf7.png)
![redpacket](https://file.fishpi.cn/2023/06/image-d0ad7756.png)
![image.png](https://pwl.stackoverflow.wiki/2022/01/image-f74aae7e.png)
![image.png](https://pwl.stackoverflow.wiki/2022/01/image-1b685256.png)

## 🔑 JetBrains OS licenses

`pwl-chat-ptyhon` had been being developed with `PyCharm IDE` under the free JetBrains Open Source license(s) granted by JetBrains s.r.o., hence I would like to express my thanks here.

<a href="https://www.jetbrains.com/?from=pwl-chat-ptyhon" target="_blank"><img src="https://b3logfile.com/file/2021/05/jetbrains-variant-2-42d96aa4.png" width="250" align="middle"/></a>
