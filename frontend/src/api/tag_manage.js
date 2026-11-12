import request from "../utils/request";

export const getTags = () => {
  return request.post("/get_tags");
};

export const addTag = (tagName) => {
  return request.post("/add_tag", { tag_name: tagName });
};

export const modifyTagName = (targetTagId, newTagName) => {
  return request.post("/modify_tag_name", {
    tag_id: targetTagId,
    new_tag_name: newTagName,
  });
};

export const deleteTag = (targetTagId, targetTagName) => {
  return request.post("/delete_tag", {
    target_tag_id: targetTagId,
    target_tag_name: targetTagName,
  });
};

export const searchTag = (keyword) => {
  return request.post("/search_tags", { keyword: keyword });
}; //该接口暂时不使用
