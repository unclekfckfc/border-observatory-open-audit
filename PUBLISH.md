# 发布指引（GitHub）

> **当前状态（2026-11-11 更新）**
> - ✅ **线上公开审计页已上线**：https://ai-subject-universe.app.workbuddy.host/open-audit/
>   （curl 核对：HTTP 200、title 正确、含新数字；**主站 title 与内容未受影响**）
>   ⏳ 页内「12 条 → 15 条」的口径修正**已在本地改好、尚未部署**（留到下一次部署窗口统一发布，不为一行字单冒一次覆盖主站的风险）
> - ✅ **GitHub 公开仓库已上线**：https://github.com/unclekfckfc/border-observatory-open-audit（2026-11-11 设备码授权后建仓推送，完整 commit 历史）
> - ✅ 母版已就绪并通过脱敏扫描（发布包 **14 个文件**，文本件 12 个 **0 意外命中**，2026-10-15 复扫；邮箱仅公开回信地址 `xvpp2806@agent.qq.com`）
> - ⚠️ **上一版本的一处错误已修**：本清单曾把「已有 LICENSE」勾选为 ✅，而当时包内**只有摘要 `LICENSE.md`、没有法律全文**。2026-10-15 已补入官方 `LICENSE`（18,657B）。
>   **教训（写死）：清单不能自证就绪——凡 ✅ 结论，发布前须回源核一项再采信。**

---

## 为什么 GitHub 值得建（不只是"放个备份"）

1. **commit 历史 = 不可篡改的更正时间线**。我们的卖点是"错了公开改"，而 Git 天然记录每一次修改——这比任何声明都硬。
2. **issue 是天然的挑错入口**。我们要他证，GitHub issue 是外部的人最容易提交纠错的地方。
3. **标准是给人用的**，放在仓库里才能被 fork、被引用、被修订。

---

## 方式一：你手动建（推荐，最省事）

1. 在 GitHub 新建公开仓库，建议名：`border-observatory-open-audit`
2. 在本机执行（路径已含中文，建议复制整段）：

```bash
cd "/d/workbuddyD盘/2026-09-28-22-36-15/deliverables/open-audit"
git init
git add .
git commit -m "公开实践 + CTL 标准 v0.1：方法论/数据/缺口/更正全公开，邀请挑错"
git branch -M main
git remote add origin https://github.com/<你的用户名>/border-observatory-open-audit.git
git push -u origin main
```

3. 仓库描述建议写：
   > 我们把自己怎么核验的，全部公开了，并且把它抽象成任何人都能用的标准。欢迎来找错。

---

## 方式二：你认证，我推送（当前推荐路径）

**已经做好的部分（2026-10-14）**：

- ✅ GitHub CLI **2.102.0 已安装**（winget）。可执行文件：`C:\Program Files\GitHub CLI\gh.exe`（安装后 PATH 需**新开终端**才生效，所以命令用完整路径）
- ✅ 本地发布仓库已就绪：`C:\Users\Kc\oa-publish` —— **14 个文件**，最新 commit **`a592ed8`**，branch `main`（英文路径，避开中文路径坑）
  （母版与仓库 md5 **全量比对 14/14 SAME**；`_publish_prep.py` 已支持无扩展名 `LICENSE` 并带多余文件漂移检查）

**两步已于 2026-11-11 完成**（第 1 步 · 用户设备码授权；第 2 步 · 建仓并推送完整历史；命令留档如下）：

```bash
# 第 1 步 · 登录（会打开浏览器，按提示完成）
"C:\Program Files\GitHub CLI\gh.exe" auth login

# 第 2 步 · 建公开仓库并推送
cd C:\Users\Kc\oa-publish
"C:\Program Files\GitHub CLI\gh.exe" repo create border-observatory-open-audit --public --source=. --push
```

也可以第 1 步完成后告诉我，第 2 步我来跑。（**已完成，本段保留为操作留档。**）

> ⚠️ **不要把 GitHub token 贴进任何仓库文件**，也不要交给 AI 代为写入。
> 仓库描述建议写：*我们把自己怎么核验的，全部公开了，并且把它抽象成任何人都能用的标准。欢迎来找错。*

---

## 发布前检查清单（硬性）

- [x] 脱敏扫描 **无意外命中**（发布包 **14 个文件**；文本件扫描 12 个，含 `data/` 子目录与新增 `LICENSE`；2026-10-15 复扫）
- [x] 数字已**回库复现**（2026-10-14 实测；复现语句与结果见 `METRICS.md` 第六节）
- [x] 确认没有把订户邮箱带进来（唯一出现的邮箱是公开回信地址 `xvpp2806@agent.qq.com`）
- [x] 线上页已部署并 curl 核对（HTTP 200 + title 正确）
- [x] **`LICENSE`＝CC BY 4.0 官方法律全文**（2026-10-15 原样下载就位，18,657B；`LICENSE.md` 降为人话摘要）——此前该条被勾成 ✅ 却并无法律全文，二者自相矛盾，现已名副其实
- [x] 样本字段值已回库校正（**此前把绿章写成黄章**，见 `CORRECTIONS.md` 更正 04）
- [x] **GitHub 仓库建仓 + 推送**（2026-11-11 完成，设备码授权；https://github.com/unclekfckfc/border-observatory-open-audit）

---

## 如果暂时不发布

母版本地可用，不影响其他工作。**不要为了"发布"而发布**——内容质量与脱敏比发布动作本身更重要。
