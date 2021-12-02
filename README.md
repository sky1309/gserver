# simple-game-server
tcp游戏服务器，客户端发送服务器指定格式的数据格式，服务端解析出协议号，分发到不同的路由中
最近看了golang实现的轻量级tcp服务器 [```zinx```](https://github.com/aceld/zinx)，学习了他实现的实现思想，做了个python的实现版本。。。

## Protocol(协议)
```
-------------------------------------------------------------------------
  2 byte msg length       2 byte msg id(route id)  + msg
         [][]                 [][]....[][][]
-------------------------------------------------------------------------
```

## Quick Start

### Install
    git clone 

    cd workspace
    
    pipenv sync

### Usage
```python
# Server


```

```python
# Test Python Client

```
