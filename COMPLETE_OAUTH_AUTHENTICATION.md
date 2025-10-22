# 🔐 Complete Google OAuth Authentication

## Current Status ✅

Your Google Calendar MCP server is running successfully! The logs show:

```
✅ Creating OAuth credentials file from environment variables...
✅ Starting Google Calendar MCP Server in HTTP mode...
✅ Google Calendar MCP Server listening on http://0.0.0.0:3000
⚠️  No valid normal user authentication tokens found.
```

**The server is working - you just need to complete the OAuth authentication.**

## 🚀 Authentication Steps

### Step 1: Access the Container Terminal

In your Coolify dashboard:
1. Go to your project
2. Find the `google-calendar-mcp` service
3. Click on **"Terminal"** or **"Exec"** to access the container

### Step 2: Run the Authentication Command

In the container terminal, run:
```bash
npm run auth
```

### Step 3: Complete OAuth Flow

The command will display something like:
```
Please visit the following URL to authorize the application:
https://accounts.google.com/o/oauth2/auth?client_id=...&redirect_uri=http://localhost:3500/oauth2callback&...
```

**Important Steps:**
1. **Copy the entire URL** from the terminal
2. **Open the URL in your browser**
3. **Sign in with your Google account** (the one you added as a test user)
4. **Grant calendar permissions** when prompted
5. **Wait for the success message** in the terminal

### Step 4: Verify Authentication Success

After completing the OAuth flow, you should see:
```
✅ Authentication successful!
✅ Tokens saved to /home/nodejs/.config/google-calendar-mcp/tokens.json
```

### Step 5: Restart the Service (if needed)

If the authentication doesn't take effect immediately:
1. In Coolify, restart the `google-calendar-mcp` service
2. Wait for it to start up
3. Check the logs - you should no longer see the "No valid tokens" warning

## 🔍 Expected Success Logs

After authentication, your logs should show:
```
✅ Google Calendar MCP Server listening on http://0.0.0.0:3000
✅ Authentication tokens loaded successfully
✅ Ready to handle calendar requests
```

## 🐛 Troubleshooting

### Issue: "Error 403: access_denied"
**Solution**: You already added yourself as a test user, but wait 10-15 minutes for Google's systems to propagate the change.

### Issue: Authentication URL doesn't work
**Solutions**:
1. **Use incognito/private browsing** mode
2. **Try a different browser** (Chrome/Edge work best)
3. **Ensure you're using the exact email** you added as a test user
4. **Wait longer** for test user propagation

### Issue: "This app isn't verified"
**Solution**: 
1. Click **"Advanced"**
2. Click **"Go to Voice_Agent (unsafe)"**
3. This is normal for apps in testing mode

### Issue: Port 3500 not accessible
**Solution**: The OAuth flow should work even in the container environment. If it doesn't, try:
1. **Copy the URL exactly** as shown
2. **Replace `localhost:3500`** with your Coolify domain if needed
3. **Contact me** if the redirect doesn't work

## 📋 Quick Checklist

- [ ] Access google-calendar-mcp container terminal in Coolify
- [ ] Run `npm run auth`
- [ ] Copy the OAuth URL from terminal output
- [ ] Open URL in browser (incognito mode recommended)
- [ ] Sign in with the Google account you added as test user
- [ ] Grant calendar permissions
- [ ] Wait for "Authentication successful" message
- [ ] Restart service if needed
- [ ] Verify logs show successful token loading

## 🎯 After Authentication Success

Once authentication is complete:
1. **The MCP transport error may persist** (that's a separate compatibility issue)
2. **But the OAuth authentication will be working**
3. **You can test calendar functionality** directly via the container
4. **The tokens will be saved** for future use

## 📞 Next Steps

1. **Complete the OAuth authentication** using the steps above
2. **Verify authentication success** in the logs
3. **Test calendar functionality** if possible
4. **Let me know the results** so we can proceed with the integration

The OAuth authentication is the critical step - once this is done, the calendar service will be properly authenticated and ready to use!