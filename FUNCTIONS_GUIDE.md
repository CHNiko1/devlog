## Like & Repost Functions Location Guide 📍

### Where are Like and Repost?

**File:** [routes.py](routes.py)

**Like Function:**
- **Route:** `/post/<post_id>/like`
- **Line:** Around line 213
- **What it does:** User can like a post, like again to unlike (toggle)
- **Need to be logged in:** YES

**Repost Function:**
- **Route:** `/post/<post_id>/repost`  
- **Line:** Around line 244
- **What it does:** User can repost a post, repost again to un-repost (toggle)
- **Need to be logged in:** YES

---

## How to Use Like and Repost in Templates

In your HTML templates (like `post_detail.html`), you can add buttons:

### Like Button
```html
<form method="POST" action="/post/{{ post.id }}/like" style="display: inline;">
    <button type="submit" class="btn btn-heart">
        ❤️ Like
    </button>
    <small>{{ post.likes|length }} likes</small>
</form>
```

### Repost Button
```html
<form method="POST" action="/post/{{ post.id }}/repost" style="display: inline;">
    <button type="submit" class="btn btn-repost">
        🔄 Repost
    </button>
    <small>{{ post.reposts|length }} reposts</small>
</form>
```

---

## New: Clear Filters Feature ✨

Added a new "Clear Filters" button for the search page!

**Route:** `/posts/clear-filters`
**What it does:** Removes all search filters and shows all posts

### In your posts.html template:

```html
{% if filters.q or filters.language or filters.level %}
    <div class="alert alert-info">
        <p>Active Filters:</p>
        {% if filters.q %}<span>Search: "{{ filters.q }}"</span>{% endif %}
        {% if filters.language %}<span>Language: {{ filters.language }}</span>{% endif %}
        {% if filters.level %}<span>Level: {{ filters.level }}</span>{% endif %}
        
        <a href="/posts/clear-filters" class="btn btn-secondary">✖ Clear All Filters</a>
    </div>
{% endif %}
```

---

## Quick Function Summary

| Route | Type | Purpose | Auth Required |
|-------|------|---------|---------------|
| `/post/<id>/like` | POST | Like/Unlike a post | YES |
| `/post/<id>/repost` | POST | Repost/Un-repost | YES |
| `/posts/clear-filters` | GET | Remove all filters | NO |

---

## How the Filter Info Works

The `filters` dictionary is now passed to the template with:
- `filters.q` - Search query
- `filters.language` - Selected language
- `filters.level` - Selected level

This lets you show users what filters are active!
