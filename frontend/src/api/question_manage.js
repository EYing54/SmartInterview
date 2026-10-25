import request from "../utils/request";

export const getQuestionList = (page, size) => {
  return request.post("/get_questions", {
    page: page,
    size: size,
  });
};

export const addQuestions = (question, answer, tag_ids) => {
  return request.post("/add_questions", {
    question: question,
    answer: answer,
    tag_ids: tag_ids,
  });
};
