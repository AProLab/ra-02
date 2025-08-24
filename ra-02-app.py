import sqlite3
import streamlit as st
from openai import OpenAI


class Database:
    """SQLite 메모리 DB 관리"""

    def __init__(self):
        self.conn = sqlite3.connect(":memory:")
        self.cursor = self.conn.cursor()
        self._initialize_db()

    def _initialize_db(self):
        self.cursor.execute(
            "CREATE TABLE texts (id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT)"
        )
        texts = [
            ("파이썬은 프로그래밍 언어입니다."),
            ("SQLite는 가벼운 데이터베이스입니다."),
            ("RAG는 검색과 생성 모델을 결합한 방법입니다."),
            ("머신러닝은 재미있는 분야입니다."),
            ("자연어 처리는 생성 작업을 포함합니다."),
        ]
        self.cursor.executemany("INSERT INTO texts (content) VALUES (?)", [(t,) for t in texts])
        self.conn.commit()

    def fetch_all(self):
        self.cursor.execute("SELECT content FROM texts")
        return [row[0] for row in self.cursor.fetchall()]

    def search(self, keyword: str):
        self.cursor.execute("SELECT content FROM texts WHERE content LIKE ?", ("%" + keyword + "%",))
        return [row[0] for row in self.cursor.fetchall()]


class AnswerGenerator:
    """OpenAI 모델을 통한 답변 생성"""

    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def generate(self, keyword: str, retrieved_texts: list[str]) -> str:
        context = "\n".join(retrieved_texts)
        prompt = f"다음 정보를 참고하여 질문에 답해 주세요:\n{context}\n\n질문: {keyword}\n 답변:"

        response = self.client.responses.create(
            model="gpt-4o",
            input=prompt,
        )
        return response.output_text


class TextApp:
    """Streamlit UI 클래스"""

    def __init__(self):
        self.db = Database()

    def run(self):
        st.header("DB 내용 조회")
        api_key = st.text_input("OPENAI API KEY를 입력하세요.", type="password")
        
        all_texts = self.db.fetch_all()
        st.markdown("**DB에 저장된 문장**")
                    
        for text in all_texts:
            st.markdown(text)

        keyword = st.text_input("검색 키워드를 입력하세요.")

        if st.button("답변 확인"):
            if not api_key or not keyword:
                st.warning("API 키와 검색 키워드를 모두 입력해주세요.")
                return

            with st.spinner("DB를 조회해 답변을 생성 중입니다..."):
                try:                   
                    retrieved_texts = self.db.search(keyword)
                    generator = AnswerGenerator(api_key)
                    answer = generator.generate(keyword, retrieved_texts)

                    st.markdown("**:red[키워드 검색 결과]**")

                    for text in retrieved_texts:
                        st.markdown(text)
                        
                    st.markdown("**:blue[검색 결과를 이용해 생성된 문장]**")
                    st.markdown(answer)
                except Exception as e:
                    st.error(f"오류 발생: {e}")


if __name__ == "__main__":
    app = TextApp()
    app.run()
