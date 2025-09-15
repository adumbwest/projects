chrome.bookmarks.onCreated.addListener((id, bookmark) => {
  chrome.bookmarks.getChildren(bookmark.parentId, (children) => {
    if (children.length > 1) {
      chrome.bookmarks.move(id, {
        parentId: bookmark.parentId,
        index: 0
      });
    }
  });
});
