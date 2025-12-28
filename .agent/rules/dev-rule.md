---
trigger: always_on
---

1. 開発の際はruffやmypyの型チェック、 DEVELOPMENT_GUIDE.md に記載されているpytestに合格する必要があります。
2. 安全性はNanaSQLiteを安心して利用してもらうために大切です。そこでOSV-Scannerと .github\workflows\security.yml のセキュリティテストに合格する必要があります。
3. docsやCHANGELOG、READMEの整備と更新も非常に大切です。