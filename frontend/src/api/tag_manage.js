import request from "../utils/request";

export const getTags = () => {
  return request.post("/get_tags");
};

export const addTag = (tag_name) => {
  return request.post("/add_tag", { tag_name: tag_name });
};

export const modifyTagName = (tag_id, new_tag_name) => {
  return request.post("/modify_tag_name", {
    tag_id: tag_id,
    new_tag_name: new_tag_name,
  });
};

export const deleteTag = (tag_id, target_tag_name) => {
  return request.post("/delete_tag", {
    tag_id: tag_id,
    target_tag_name: target_tag_name,
  });
};

export const searchTag = (keyword) => {
  return request.post("/search_tags", { keyword: keyword });
};
