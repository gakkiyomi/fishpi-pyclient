  ![摸鱼派cn.png](https://b3logfile.com/file/2023/05/摸鱼派-cn-owZQT8f.png)

# pwl-chat-python

> 摸鱼派聊天室 python 命令行客户端

基于摸鱼打工人社区——摸鱼派开放 API 开发的摸鱼派聊天室 python 客户端程序，可以在里面边写 Bug 边愉快地吹水摸鱼。

## 安装

环境: Python3.9 以上

执行

```bash
pip install pwl-chat-python
```

## 运行

```bash
pwl-chat-python -u username -p password -c <两步验证码>
```

## 调试

如果你已安装,请先卸载，否则启动调试会执行安装好的包

```bash
python core.py
```

## 功能

- 💬 聊天模式
  - 💬 聊天吹水
  - 🤖️ 自动复读
  - 🤖️ 自动领取昨日奖励
  - 🧠 自言自语
    - 自定义语句池
    - 定时发送
  - 🧧 自动化抢红包（脚本哥）
    - 自定义抢红包延时
    - 心跳红包防止踩坑
    - 心跳红包风险预测
    - ~~猜拳红包百分百胜率~~
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
    - 发红包🧧
      - 拼手气红包
      - 普通红包
      - 专属红包
      - 心跳红包
      - 猜拳红包
      - 设置抢红包等待时间
      - 抢猜拳红包最大限制

## 效果

![image.png](https://file.fishpi.cn/2023/06/image-d4da9bf7.png)
![redpacket](https://file.fishpi.cn/2023/06/image-d0ad7756.png)
![image.png](https://pwl.stackoverflow.wiki/2022/01/image-f74aae7e.png)
![image.png](https://pwl.stackoverflow.wiki/2022/01/image-1b685256.png)
