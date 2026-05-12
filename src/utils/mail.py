"""
邮件发送模块

提供 SMTP 邮件发送功能，支持普通文本邮件。

支持以下 SMTP 端口和协议：
- 465: SMTP over SSL (推荐)
- 587: SMTP with STARTTLS
- 其他端口: 普通 SMTP 连接

Usage:
    基础用法：

    ```python
    from src.core.mail import Mail

    # 创建邮件客户端实例
    mail = Mail(
        server="smtp.example.com",
        port=465,
        username="noreply@example.com",
        password="your_password",
        nickname="系统通知",
    )

    # 发送邮件
    mail.send_plain(
        receivers=["user@example.com"],
        subject="测试邮件",
        body="这是一封测试邮件",
    )

    # 发送给多个收件人
    mail.send_plain(
        receivers=["user1@example.com", "user2@example.com"],
        subject="群发邮件",
        body="这是一封群发邮件",
    )
    ```

    异步用法（配合 FastAPI）：

    ```python
    from fastapi import BackgroundTasks

    def send_notification(email: str):
        mail = Mail(
            server="smtp.example.com",
            port=465,
            username="noreply@example.com",
            password="your_password",
        )
        mail.send_plain(
            receivers=[email],
            subject="通知",
            body="您有一条新通知",
        )

    @app.post("/register")
    async def register(request: Request, background_tasks: BackgroundTasks):
        # 注册逻辑...
        background_tasks.add_task(send_notification, request.email)
        return {"message": "注册成功"}
    ```
"""

import smtplib
from email.header import Header
from email.mime.text import MIMEText
from email.utils import formataddr


class Mail:
    """SMTP 邮件发送客户端

    Attributes:
        host: SMTP 服务器地址
        port: SMTP 服务器端口
        user: 邮箱用户名（发件人邮箱）
        password: 邮箱密码或授权码
        nickname: 发件人昵称（可选，用于显示友好的发件人名称）
    """

    def __init__(
        self,
        server: str,
        port: int,
        username: str,
        password: str,
        nickname: str | None = None,
    ) -> None:
        """初始化邮件客户端

        Args:
            server: SMTP 服务器地址，如 "smtp.gmail.com" 或 "smtp.qq.com"
            port: SMTP 端口号，常用值：
                - 465 (SMTP over SSL)
                - 587 (SMTP with STARTTLS)
                - 25 (普通 SMTP，不推荐)
            username: 发件人邮箱地址
            password: 邮箱密码或授权码（如 QQ 邮箱的授权码）
            nickname: 发件人显示昵称，如 "系统管理员"（可选）
        """
        self.host: str = server
        self.port: int = int(port)
        self.user: str = username
        self.password: str = password
        self.nickname: str | None = nickname

    def connect(self) -> smtplib.SMTP:
        """创建并连接 SMTP 服务器

        根据端口号自动选择连接方式：
        - 465: 使用 SMTP_SSL 建立 SSL 连接
        - 587: 使用 STARTTLS 加密连接
        - 其他: 普通 TCP 连接

        Returns:
            已登录的 SMTP 服务器实例

        Raises:
            smtplib.SMTPException: 连接或登录失败时抛出异常
        """
        if self.port == 465:
            # 端口 465 使用 SSL 加密连接
            server = smtplib.SMTP_SSL(self.host, self.port)
        elif self.port == 587:
            # 端口 587 使用 STARTTLS 升级到加密连接
            server = smtplib.SMTP(self.host, self.port)
            _ = server.ehlo()
            _ = server.starttls()
        else:
            # 其他端口使用普通连接
            server = smtplib.SMTP(self.host, self.port)
        # 登录 SMTP 服务器
        _ = server.login(self.user, self.password)
        return server

    def send_plain(
        self,
        receivers: list[str] | str,
        subject: str,
        body: str,
    ) -> None:
        """发送纯文本邮件

        Args:
            receivers: 收件人邮箱地址列表，或单个邮箱地址字符串
            subject: 邮件主题
            body: 邮件正文内容（纯文本）

        Raises:
            smtplib.SMTPException: 发送失败时抛出异常

        Note:
            - 发送完成后会自动关闭服务器连接
            - 建议使用 try-finally 确保连接被正确关闭
        """
        server = self.connect()
        # 创建 MIME 文本邮件，plain 表示纯文本
        msg = MIMEText(body, "plain", "utf-8")
        # 设置邮件主题（使用 UTF-8 编码避免乱码）
        msg["Subject"] = str(Header(subject, "utf-8"))
        # 设置发件人，显示格式为 "昵称 <邮箱地址>"
        msg["From"] = (
            formataddr((self.nickname, self.user)) if self.nickname else self.user
        )
        # 发送邮件并关闭连接
        _ = server.sendmail(self.user, receivers, msg.as_string())
        _ = server.quit()
