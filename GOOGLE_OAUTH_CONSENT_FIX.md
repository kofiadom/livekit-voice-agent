# 🔐 Fix Google OAuth Consent Screen Error 403

## Error Analysis

You're getting this error:
```
Voice_Agent has not completed the Google verification process. The app is currently being tested, and can only be accessed by developer-approved testers.
Error 403: access_denied
```

**Root Cause**: Your OAuth consent screen is in "Testing" mode and your email is not added as a test user.

## 🚀 Solution Steps

### Step 1: Add Yourself as a Test User

1. **Go to Google Cloud Console**: https://console.cloud.google.com
2. **Select your project**: `vaulted-journal-475910-f8`
3. **Navigate to OAuth consent screen**:
   - Go to **APIs & Services** → **OAuth consent screen**
4. **Add test users**:
   - Scroll down to **"Test users"** section
   - Click **"+ ADD USERS"**
   - Add your email address (the one you'll use for authentication)
   - Click **"SAVE"**

### Step 2: Wait for Propagation (Important!)

- **Wait 5-10 minutes** for the test user to propagate through Google's systems
- This is crucial - immediate authentication attempts often fail

### Step 3: Try Authentication Again

After waiting, run the authentication command again:
```bash
npx @cocal/google-calendar-mcp auth
```

## 🔄 Alternative Solution: Publish the App (Recommended)

If you want to avoid the weekly re-authentication and test user limitations:

### Option A: Publish to Production (No Verification Needed)

1. **Go to OAuth consent screen** in Google Cloud Console
2. **Click "PUBLISH APP"** button
3. **Confirm** the publishing
4. **Accept** that users will see an "unverified app" warning

**Benefits:**
- ✅ No test user limitations
- ✅ Tokens don't expire after 7 days
- ✅ Anyone can authenticate (if you share the app)

**Trade-off:**
- ⚠️ Users see "This app isn't verified" warning during OAuth flow
- ⚠️ They need to click "Advanced" → "Go to Voice_Agent (unsafe)" to proceed

### Option B: Keep in Testing Mode

If you prefer to keep it in testing mode:
- ✅ No scary warnings for users
- ❌ Must add each user as a test user
- ❌ Tokens expire after 7 days
- ❌ Limited to 100 test users

## 🔍 Verification Steps

After adding yourself as a test user (and waiting):

1. **Check test user list**:
   - Go to OAuth consent screen
   - Verify your email appears in "Test users" section

2. **Test authentication**:
   ```bash
   npx @cocal/google-calendar-mcp auth
   ```

3. **Expected flow**:
   - OAuth URL opens in browser
   - You see Google sign-in page
   - After signing in, you see permission request
   - Grant calendar permissions
   - Authentication completes successfully

## 🐛 Troubleshooting

### Still getting 403 after adding test user?
- **Wait longer**: Sometimes takes up to 15 minutes
- **Clear browser cache**: Try incognito/private browsing
- **Check email**: Ensure you're using the exact email added as test user
- **Verify project**: Make sure you're in the correct Google Cloud project

### "This app isn't verified" warning?
- This is normal for unpublished apps
- Click **"Advanced"** → **"Go to Voice_Agent (unsafe)"**
- Or publish the app to production mode

### Authentication URL not working?
- **Check redirect URI**: Should be `http://localhost:3500/oauth2callback`
- **Verify port**: Make sure port 3500 is available
- **Try different browser**: Some browsers block localhost redirects

## 📋 Quick Checklist

- [ ] Added your email as test user in Google Cloud Console
- [ ] Waited 5-10 minutes for propagation
- [ ] Using the correct email for authentication
- [ ] Port 3500 is available on your system
- [ ] Browser allows localhost redirects

## 🎯 Recommended Approach

**For Production Use**: Publish the app to avoid test user limitations
**For Development**: Add yourself as test user and wait for propagation

## 📞 Next Steps

1. **Add yourself as test user** in Google Cloud Console
2. **Wait 10 minutes** for propagation
3. **Try authentication again**
4. **If successful**, proceed with calendar integration testing
5. **Consider publishing app** for production use

Your Google Calendar integration will work perfectly once this OAuth consent issue is resolved!