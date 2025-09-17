from typing import List, Optional
from fastapi import FastAPI, HTTPException, status
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID, uuid4

app = FastAPI()

class Answer(BaseModel):
  id: Optional[UUID] = Field(default_factory=uuid4)
  answer: str
  votes: int = 0

class Question(BaseModel):
  id: Optional[UUID] = Field(default_factory=uuid4)
  question: str
  answers: List[Answer]

class Poll(BaseModel):
  id: Optional[UUID] = Field(default_factory=uuid4)
  name: str
  questions: List[Question]
  created_at: Optional[str] = None
  updated_at: Optional[str] = None

db: List[Poll] = [
  Poll(name="Poll", created_at=str(datetime.now()), questions=[
    Question(question="Jaki kolor ściany wybrać?", answers=[
      Answer(answer="Czerwony"),
      Answer(answer="Zielony"),
      Answer(answer="Niebieski"),
    ]),
    Question(question="Idziemy dziś na piwo?", answers=[
      Answer(answer="Tak"),
      Answer(answer="Nie")
  ])])
]

# Utwórz nową ankietę
@app.post("/v1/polls", status_code=status.HTTP_201_CREATED)
async def create_poll(poll: Poll):
  poll.created_at = datetime.now()
  db.append(poll)
  return poll
  
# Pobierz wszystkie ankiety
@app.get("/v1/polls")
async def fetch_pools():
  return db
  
# Pobierz ankietę po ID
@app.get("/v1/polls/{poll_id}")
async def fetch_poll(poll_id: str):
  for poll in db:
    if str(poll.id) == poll_id:
      return poll
  raise HTTPException(status_code=404, detail="Poll not found")

# Dodaj odpowiedź do pytania
@app.post("/v1/polls/{poll_id}/vote")
async def vote(poll_id: str, question_id: str, answer_id: str):
  for poll in db:
    if str(poll.id) == poll_id:
      for question in poll.questions:
        if str(question.id) == question_id:
          for answer in question.answers:
            if str(answer.id) == answer_id:
              answer.votes += 1
              poll.updated_at = datetime.now()
              return answer
  raise HTTPException(status_code=404, detail="Answer not found")

# Dodaj pytanie do ankiety
@app.post("/v1/polls/{poll_id}/questions", status_code=status.HTTP_201_CREATED)
async def add_question(poll_id: str, question: Question):
  for poll in db:
    if str(poll.id) == poll_id:
      poll.questions.append(question)
      poll.updated_at = datetime.now()
      return poll
  raise HTTPException(status_code=404, detail="Poll not found")

# Usuń pytanie z ankiety
@app.delete("/v1/polls/{poll_id}/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_question(poll_id: str, question_id: str):
  for poll in db:
    if str(poll.id) == poll_id:
      for question in poll.questions:
        if str(question.id) == question_id:
          poll.questions.remove(question)
          poll.updated_at = datetime.now()
          return None
  raise HTTPException(status_code=404, detail="Question not found")

# Aktualizuj pytanie
@app.put("/v1/polls/{poll_id}/questions/{question_id}", status_code=status.HTTP_200_OK)
async def update_question(poll_id: str, question_id: str, question: Question):
  for poll in db:
    if str(poll.id) == poll_id:
      for q in poll.questions:
        if str(q.id) == question_id:
          if question.question:
            q.question = question.question
          if question.answers:
            q.answers = question.answers
          poll.updated_at = datetime.now()
          return poll
  raise HTTPException(status_code=404, detail="Question not found")

# Usuń ankietę
@app.delete("/v1/polls/{poll_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_poll(poll_id: str):
  for poll in db:
    if str(poll.id) == poll_id:
      db.remove(poll)
      return poll
  raise HTTPException(status_code=404, detail="Poll not found")

# Pobierz wyniki ankiety
@app.get("/v1/polls/{poll_id}/results")
async def get_results(poll_id: str):
  for poll in db:
    if str(poll.id) == poll_id:
      results = []
      for question in poll.questions:
        answers = []
        for answer in question.answers:
          answers.append({
            "answer": answer.answer,
            "votes": answer.votes
          })
        results.append({
          "question": question.question,
          "answers": answers
        })
      return results
  raise HTTPException(status_code=404, detail="Poll not found")