---
layout: default
title: Archive
permalink: /archive/
---
<h1>Tags</h1>

{% assign tags = site.tags | sort %}
{% if tags.size > 0 %}
<div class="tag-list">
  {% for tag in tags %}
  <a href="#tag-{{ tag[0] | slugify }}" class="tag-pill">{{ tag[0] }} <span class="tag-count">{{ tag[1].size }}</span></a>
  {% endfor %}
</div>

{% for tag in tags %}
<h2 id="tag-{{ tag[0] | slugify }}">{{ tag[0] }}</h2>
<ul class="post-list">
  {% for post in tag[1] %}
  <li>
    <span class="post-meta">{{ post.date | date: "%B %-d, %Y" }}</span>
    <a href="{{ post.url | relative_url }}">{{ post.title }}</a>
  </li>
  {% endfor %}
</ul>
{% endfor %}
{% else %}
<p>No tags yet.</p>
{% endif %}

<h1>By Date</h1>

{% assign posts_by_year = site.posts | group_by_exp: "post", "post.date | date: '%Y'" %}
{% for year in posts_by_year %}
<h2>{{ year.name }}</h2>
<ul class="post-list">
  {% for post in year.items %}
  <li>
    <span class="post-meta">{{ post.date | date: "%B %-d, %Y" }}</span>
    <a href="{{ post.url | relative_url }}">{{ post.title }}</a>
  </li>
  {% endfor %}
</ul>
{% endfor %}
