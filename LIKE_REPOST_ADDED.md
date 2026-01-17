## ✅ Like and Repost Functions Added to Frontend!

I've added **Like** and **Repost** buttons to all post pages. Now you can like and repost directly from:

### 📍 Where Like/Repost Buttons Are:

1. **Home Page** (`templates/index.html`)
   - Featured posts section shows like and repost counts
   - Click to like/repost any featured post

2. **Posts Page** (`templates/posts.html`)
   - Every post in the list has like and repost buttons
   - Shows count of likes and reposts
   - Works with filters and search

3. **Post Detail Page** (`templates/post_detail.html`)
   - Large like and repost buttons at the top
   - Shows counts right next to buttons
   - Clear visual feedback when you already liked/reposted

### 🎯 How They Work:

**Like Button:**
- 🤍 Empty heart when not liked
- ❤️ Full red heart when already liked by you
- Click again to unlike

**Repost Button:**
- ↗️ Arrow when not reposted
- 🔄 Refresh icon when already reposted by you
- Click again to remove repost

### 👤 Logged In Users:
- Can click buttons directly
- See buttons highlight when they've already interacted
- Get success messages

### 🔐 Not Logged In:
- Buttons are clickable but redirect to login
- Must create account or login first

### 📊 Stats Shown:
- Each button shows the count: `🤍 5 likes` or `🔄 3 reposts`
- Updates automatically after each action

### 🔧 Backend Routes:
- `/post/<post_id>/like` - Like or unlike
- `/post/<post_id>/repost` - Repost or un-repost
- Both are POST requests (secure)

### 🗄️ Database Models:
- `Like` model - stores post likes
- `Repost` model - stores post shares
- Both track who liked/reposted which post
- Prevents duplicate likes/reposts per user

Everything is ready to use! Just refresh your browser if it's running.
