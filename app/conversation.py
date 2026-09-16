from utils.logging import get_logger
import os
import json
logger=get_logger(__name__)


class ConversationMemory:
    def __init__(self,max_history=2):
        self.history=[]
        self.summary=""
        self.max_history=max_history

        self.memory_dir="memory"
        self.memory_file=os.path.join(self.memory_dir,"conversation.json")

        os.makedirs(self.memory_dir,exist_ok=True)
        self.load_memory()

        logger.info("Conversation memory initialized - max history: %s",self.max_history)

    def add_conversation(self,question,answer):
            if question is None or not str(question).strip():
                logger.warning("conversation not saved: question is empty")
                return

            if answer is None or not str(answer).strip():
                logger.warning("conversation not saved: answer is empty")
                return

            question=str(question).strip()
            answer=str(answer).strip()

            self.history.append({
                "question":question,
                "answer":answer
            })

            logger.info("conversation added - history size: %s",len(self.history))

            while len(self.history)>self.max_history:
                old_conversation=self.history.pop(0)

                old_question=old_conversation.get("question","")
                old_answer=old_conversation.get("answer","")

                old_text=(
                    f"User: {old_question}\n"
                    f"Assistant: {old_answer}"
                )

                if self.summary:
                    self.summary+="\n"+old_text

                else:
                    self.summary=old_text

                logger.info("old conversation moved to memory summary")

            self.save_memory()
            logger.info("Memory updated - summary chars: %s, recent conversations: %s",
                            len(self.summary),len(self.history))


    def save_memory(self):
        data={
            "summary":self.summary,
            "history":self.history
        }

        with open(self,self.memory_file,"w",encoding="utf-8")as file:
            json.dump(data,file,indent=4)
        
        logger.info("Conversation memory saved to: %s",self.memory_file)

    def load_memory(self):
        if not os.path.exists(self.memory_file):
            logger.info("No previous conversation memory found")
            return
        try:
            with open(self.memory_file,"r",encoding="utf-8")as file:
                data=json.load(file)
            self.summary=data.get("summary","")
            self.history=data.get("history",[])

            logger.info(
                "Conversation memory loaded - summary chars: %s, recent conversations: %s",
                len(self.summary),
                len(self.history)
            )
        except Exception as e:
            logger.exception("Failed to load conversation memory: %s",e)

    def get_memory(self):
        memory=""

        if self.summary:
            memory+="Previous conversation:\n"
            memory+=self.summary

        if self.history:
            if memory:
                memory+="\n\n"

            memory+="Recent conversation:\n"

            for conversation in self.history:
                question=conversation.get("question","")
                answer=conversation.get("answer","")

                memory+=f"User: {question}\n"
                memory+=f"Assistant: {answer}\n"

        logger.info("Memory retrieved - summary chars: %s, recent conversations: %s",
            len(self.summary),
            len(self.history)
        )

        return memory