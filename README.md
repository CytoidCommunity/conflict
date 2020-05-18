# Conflict

Conflict 是一个 Bilibili Live 录屏工具。

## 使用

### 安装

#### 从 PyPI 安装（推荐）

**目前暂不支持，将会在所有功能完成之后发布到 PyPI**

```shell script
# 仅使用录屏功能
pip install conflict
# 开播提醒 - Mirai API HTTP
pip install "conflict[mirai]"
# 视频转码（需要安装ffmpeg）
pip install "conflict[ffmpeg]"
```

#### 从源代码安装

```shell script
git clone https://github.com/CytoidCommunity/conflict.git
cd conflict
pip install .
```

## 运行

conflict 使用配置文件来工作。请阅读 [配置范例](config.sample.full.toml)。

对于 Windows 7+ 用户，你的配置文件在：
```
C:\Users\<username>\AppData\Local\CytoidCommunity\conflict
```
对于 Windows XP 用户，你的配置文件在：
```
C:\Documents and Settings\<username>\Application Data\CytoidCommunity\conflict
```
对于 Mac OS X 用户，你的配置文件在：
```
~/Library/Application Support/conflict
```
对于 *nix 用户，你的配置文件在：
```
~/.config/conflict
```

然后在终端中执行：
```shell script
conflict deamon
```

如果无法运行，一般是你的配置文件有问题，请使用如下命令检查你的配置文件。
```shell script
conflict check
```

## For developers

We use [poetry](https://github.com/python-poetry/poetry) as package manager. Since `pip` support `pyproject.toml` file, so you can use virtualenv only.

Contributions & issues are welcomed.