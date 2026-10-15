-- scenes.lua: pandoc filter for the public site (run by bin/site).
--
-- * Links to .md files become links to .html files.
-- * Each "## 1." scene heading gets the id scene-1 (pandoc would give
--   "section", "section-1", ...), so site/images.txt can name a scene.
--   With --section-divs the id lands on the section the heading opens.

function Link(el)
  if not el.target:match("^%a+:") then
    el.target = el.target:gsub("%.md$", ".html"):gsub("%.md#", ".html#")
  end
  return el
end

function Header(el)
  local n = pandoc.utils.stringify(el.content):match("^(%d+)%.?$")
  if el.level == 2 and n then
    el.identifier = "scene-" .. n
    table.insert(el.classes, "scene")
  end
  return el
end
