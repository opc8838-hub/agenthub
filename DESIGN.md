# 碳基社区首页 · 视觉修订

## 参考与实现

采用用户图一的浅灰纸感、黑色展板标题、细线、点阵、蓝粉橙绿光晕及黑白线性图标。图二的大型 T-agent 由内置图像工具提取为透明 PNG，与彩色圆盘、轨道细线及投影分层排版。

字体选配遵循用户指定的 `C:/Users/Administrator/Desktop/chinese-font-selector/chinese-font-selector/SKILL.md`：中文主体、明确字号层级、正文正常字距，以大字、强字重保证现场展示的可读性。

第三版结合桌面视频 `飞书20260920-140652.qt` 的画面节奏，改为一个主题一个独立大屏：社区介绍 → 长期计划 → 负责人 / 主讲老师 → 课程成长路线 → AI 实战社群 → 产品与定制开发 → 咨询与 1V1 陪跑。桌面各区块至少占据一个可视区域（扣除顶栏）；手机按内容自然延展，不压缩字号。每屏只展示主题、关键说明、核心视觉和详情按钮，完整内容仍在原页弹窗呈现。

## 字体

- 标题：Noto Sans SC（思源黑体系），主标题字重 800，SIL OFL；来源 https://github.com/google/fonts/tree/main/ofl/notosanssc 。
- 首页主说明：20–26px，字重 550；弹窗正文桌面 20px、手机 18px。
- 英文及数字：Inter，按信息层级分配字重，SIL OFL；来源 https://github.com/google/fonts/tree/main/ofl/inter 。
- 网页使用按页面文字裁剪的本地 WOFF2，不加载全量中文字体；授权文本位于 assets 中。
- 页面内容新增汉字后，需要重新执行 `python -m fontTools.subset assets/NotoSansSC-source.ttf --text-file=index.html --flavor=woff2 --output-file=assets/community-cn.woff2 --layout-features=*`。

## 素材

- 吉祥物：`assets/t-agent-cutout.png`，RGBA，保留透明通道。
- 原始参考：`assets/t-agent.jpg`。
- 纸感：`assets/paper-grain.svg`，可重复平铺的程序化颗粒。
- 线性图标：index.html 内部 SVG symbols，共享描边体系。

### 吉祥物处理提示词

内置 image_gen，background-extraction：从用户原图仅提取上方大号挥手 T-agent；保持原本黑白平面造型、倾斜姿势、蓝色天线、T 字标记和挥手线条；移除全部底色、文字、下方四个小角色和原阴影；完整保留头、手、脚，输出真正透明的 PNG，不转为 3D。

## 文件与检查

- index.html：七个首页主题区块和 9 个站内弹窗，包括社区介绍、长期计划、五个主题、联系方式及全部主题目录。
- styles.css：纸感视觉、中文排版及响应式布局。
- app.js：弹窗、焦点限制与恢复、Esc / 遮罩关闭、微信号复制、主题滚动定位和当前章节提示。
- verify_preview.py：浏览器截图与交互验证。
- preview/：桌面、手机和弹窗实际截图。

页面不包含外部跳转或假登记成功。联系入口提供已由用户给出的微信号 allen_8838，正式表单、二维码和产品演示素材可在提供后接入。

第三版浏览器验证通过：七个桌面大屏、九个弹窗、目录定位、嵌套联系弹窗、键盘焦点与关闭操作、五种响应式宽度无横向溢出，且无 JavaScript 错误。实际截图位于 preview/，各主题单屏文件以 chapter- 开头。
