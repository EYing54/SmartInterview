import request from "../utils/request";

export const getQuestionList = (
  page,
  size,
  searchCriteria = "",
  searchKeyword = "",
) => {
  return request.post("/get_question_list", {
    page: page,
    size: size,
    search_criteria: searchCriteria,
    search_keyword: searchKeyword,
  });
};

export const addQuestions = (question, answer, tagIds) => {
  return request.post("/add_questions", {
    question: question,
    answer: answer,
    tag_ids: tagIds,
  });
};
export const deleteQuestions = (questionIds) => {
  return request.post("/delete_question", { question_ids: questionIds });
};
