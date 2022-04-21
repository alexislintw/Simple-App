# Simple-App
A simple app built with FastAPI

### Features
- Sign Up
- User Defined Password
- Email Verification
- Login
- User Profile
- Reset Password
- Cookies and Logout
- User Database Dashboard
- User Statistics

### Demo UI
- [landing page](https://simple-app-420.herokuapp.com/static/single_page.htm)
- [admin page](https://simple-app-420.herokuapp.com/static/admin.htm)

### API
- 使用到第三方認證的 API 請參考[本網頁](https://simple-app-420.herokuapp.com/static/oauth2_api.htm)
- 其他 API 請參考 [Swagger UI](https://simple-app-420.herokuapp.com/docs)

### 注意事項
- 註冊時，所指定的密碼中所含的特殊符號僅限 !@#$%^&*()_+\-=,./?
- 註冊時，會先檢查資料庫，檢查該 email 是否已經註冊過。不論之前是以 email/password 方式註冊，或是以 google account 或 facebook account 註冊, 同一個 email 不能重複註冊。
- 登入時，會先檢查資料庫，檢查該 email 是否已註冊。先前若以 email/password 方式註冊的，必須以 email/password 方式登入。
先前若以第三方帳號註冊的，則必須以第三方帳號登入。
- 註冊(Sign Up)成功則視同已登入(Logged In))，其帳號的登入次數算一次。
- active session 算法同上。

