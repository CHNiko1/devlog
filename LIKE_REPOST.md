## Like & Repost Features Added! 🎉

I've added like and repost functionality to your posts! Here's what was added:

### What Changed

**Models (models.py):**
- `Like` model - stores when users like posts
- `Repost` model - stores when users share posts
- Each can only be done once per user per post (prevents duplicates)

**Routes (routes.py):**
- `/post/<post_id>/like` - Like or unlike a post
- `/post/<post_id>/repost` - Repost or un-repost a post

### How to Use

1. First, reset the database to create the new tables:
```bash
python reset_db.py
python app.py
```

2. This will create a fresh database with:
   - `likes` table
   - `reposts` table
   - Sample data

### Features

**Likes:**
- User can like a post
- If already liked, clicking like again will unlike it (toggle)
- Shows success/info message
- Only logged-in users can like

**Reposts:**
- User can repost (share) a post
- If already reposted, clicking repost again will remove it (toggle)
- Shows success/info message
- Only logged-in users can repost

### Database Structure

**likes table:**
```
- id (primary key)
- post_id (which post was liked)
- author_id (which user liked it)
- created_at (when it was liked)
```

**reposts table:**
```
- id (primary key)
- post_id (which post was reposted)
- author_id (which user reposted it)
- created_at (when it was reposted)
```

### What You Can Do Next

In your templates, you can:
- Show count of likes: `{{ post.likes|length }}`
- Show count of reposts: `{{ post.reposts|length }}`
- Show like button: Check if current user already liked using Like.query
- Show repost button: Check if current user already reposted using Repost.query

### Important Notes

⚠️ You MUST reset the database for these to work:
```bash
python reset_db.py
```

Then run the app normally:
```bash
python app.py
```
