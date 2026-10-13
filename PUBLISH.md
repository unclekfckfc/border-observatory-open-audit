# 发布指引（GitHub）

> **当前状态（2026-10-14 更新）**
> - ✅ **线上公开审计页已上线**：https://ai-subject-universe.app.workbuddy.host/open-audit/
>   （curl 核对：HTTP 200、title 正确、含新数字；**主站 title 与内容未受影响**）
> - ⏳ **GitHub 公开仓库：CLI 已着手安装，待你完成账号认证**。本机原本无 `gh`（`command not found`），已用 winget 安装 GitHub CLI；**建仓与推送仍需你的 GitHub 授权**——我无法代替你登录。认证完成后告诉我，我可代跑 `gh repo create --public` 并推送。
> - ✅ 母版已就绪并通过脱敏扫描（**12 个文件 0 命中**）

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

## 方式二：授权我来做

如果你希望我代为推送，需要：
1. 安装 `gh` CLI，或
2. 提供一个有 `public_repo` 权限的 GitHub token（**注意：token 不要写进任何仓库文件**）

拿到授权后我可以执行 `gh repo create --public` 并推送。

---

## 发布前检查清单（硬性）

- [x] 脱敏扫描 **0 命中**（12 个文件，含 `data/` 子目录）
- [x] 数字已**回库复现**（2026-10-14 实测；复现语句与结果见 `METRICS.md` 第六节）
- [x] 确认没有把订户邮箱带进来（唯一出现的邮箱是公开回信地址 `xvpp2806@agent.qq.com`）
- [x] 线上页已部署并 curl 核对（HTTP 200 + title 正确）
- [x] 已有 `LICENSE.md`（CC BY 4.0）——**此前"无需授权"与"包内无 LICENSE"自相矛盾，已修并记入更正**
- [x] 样本字段值已回库校正（**此前把绿章写成黄章**，见 `CORRECTIONS.md` 更正 04）
- [ ] **GitHub 仓库建仓 + 推送**（唯一未完成项，待你的账号认证）

---

## 如果暂时不发布

母版本地可用，不影响其他工作。**不要为了"发布"而发布**——内容质量与脱敏比发布动作本身更重要。
