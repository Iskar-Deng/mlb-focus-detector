# mlb-focus-detector

[🇺🇸 English version](./README.md)

这是一个用于展示 MLB 实时赛况，并通过焦点值评估比赛的紧张程度的浏览器插件。

![插件界面演示](assets/popup-demo.png)

## 功能特点

- 显示比赛双方、比分、和局面  
- 使用颜色编码的焦点值（分数越高颜色越红）  
- 点击任意比赛可跳转到 MLB Gameday 页面  
- 点击焦点分可跳转到 MLB.TV 直播  

## 焦点值说明

焦点值衡量当前局面的紧张程度，算法考虑以下因素：
- 当前局数（第七局后有额外加权）
- 比分差距
- 垒包/出局数状态
- 得分对胜率的影响

焦点值最终归一化成整数，100 代表比赛开始的局面。

## 如何使用

### 手动安装插件

1. 下载并解压本仓库中的 `extension.zip`  
2. 打开 **Chrome** 或 **Edge**，进入 `chrome://extensions`  
3. 开启右上角的 **开发者模式**  
4. 点击“加载已解压的扩展程序”，选择解压后的 `extension` 文件夹  
5. 图标应会出现在浏览器工具栏中  

### 使用方式

- 点击插件图标查看当日 MLB 实时比赛  
- 点击任意比赛跳转至 **MLB Gameday 页面**  
- 点击 **焦点分** 跳转至 **MLB.TV 直播**  
- 右键插件图标可设置你最关注的球队，优先显示这些比赛  
