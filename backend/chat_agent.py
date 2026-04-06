import os, json
from dotenv import load_dotenv
from openai import AzureOpenAI
import re
from tools import Tool
from rag_index import RAGIndex
from product_engine import ProductEngine
from recommender import Recommender
from order_manager import OrderManager

load_dotenv()

class RetailChatAgent:
    def __init__(self):
        self.pending_ingredients = {}
        self.rag = RAGIndex()
        self.products = ProductEngine()
        self.recomm = Recommender()
        self.order_manager = OrderManager()

        self.client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_KEY"),
            api_version="2024-02-15-preview",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )

        self.tools = {
            "rag_search": Tool("rag_search", "Semantic search using RAG", self.rag.search),
            "ingredients": Tool("ingredients", "List ingredients", self.products.get_ingredients),
            "product_search": Tool("product_search", "Search dishes", self.products.search_products),
            "recommend": Tool("recommend", "Recommend dishes", self.recomm.recommend),
            "order": Tool("order", "Place an ingredient order", lambda user_id: self._place_order(user_id)), 
            "history": Tool("history", "Retrieve order history", self.order_manager.get_order_history),
            "decline_order": Tool("decline_order", "Decline the order", lambda user_id: self._decline_order(user_id)),

        }
    
    def _place_order(self, user_id):
        ingredients = self.pending_ingredients.get(user_id)   

        if not ingredients:
            return "There are no ingredients to order."

        # ✅ Save the order in orders.json
        self.order_manager.save_order(user_id, ingredients)

        # Clear pending
        del self.pending_ingredients[user_id]

        return (
            "✅ Your order has been placed!\n\n"
            "Ordered items:\n- " + "\n- ".join(ingredients)
            )
    def _decline_order(self, user_id):
        # Remove any stored ingredients
        if user_id in self.pending_ingredients:
            del self.pending_ingredients[user_id]

            return "👍 No problem! I won't order the ingredients. Let me know if you need anything else."
    
    def extract_ingredients_from_text(self, text):
            ingredients = []

            for line in text.split("\n"):
                cleaned = line.strip()

                # Bullet points
                if cleaned.startswith(("-", "*", "•")):
                    ingredients.append(cleaned.lstrip("-*• ").strip())
                    continue

                # Measurement-based ingredients
                if re.search(r"\b(cup|cups|tsp|tbsp|tablespoon|teaspoon|gram|kg|ml|sprig|cloves?)\b",
                            cleaned, re.IGNORECASE):
                    ingredients.append(cleaned.strip())
                    continue

            return ingredients



    def decide(self, msg):
        
        # If user is confirming an order:
        if msg.strip().lower() in ["yes", "sure", "ok", "okay", "please do", "go ahead"]:
            return {"tool": "order", "argument": "local-user"}
        
        if msg.strip().lower() in ["no", "nope", "not now", "dont", "don't", "no thanks"]:
            return {"tool": "decline_order", "argument": "local-user"}


        system_prompt = (
            
        "You are a tool routing assistant.\n\n"

        "IMPORTANT ROUTING RULES:\n"
        "- ALWAYS choose 'rag_search' when the user asks about ANY dish, recipe, cuisine, "
        "food name, or ingredients of a dish.\n"
        "- Only choose 'ingredients' AFTER 'rag_search' has already succeeded.\n"
        "- If the user asks for similar dishes, choose 'recommend'.\n"
        "- If the user asks to Place ingredient order, choose 'order'.\n"
        "- If the user asks to look up a dish by name only, choose 'product_search'.\n\n"

        "IF YOU ARE NOT 100% CERTAIN, ALWAYS choose 'rag_search'.\n\n"

        "Return ONLY JSON: {\"tool\":\"tool_name\", \"argument\":\"text\"}"

        )

        r = self.client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT"),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": msg},
            ],
            response_format={"type": "json_object"},
        )
        return json.loads(r.choices[0].message.content)

    
    
    def run(self, action):
        tool = action["tool"]
        arg = action["argument"]

        # If previous turn asked user to confirm order
        # Check if user response is "yes"
        
        if tool == "order":
            return self._place_order(arg) 
        
        
        if tool == "decline_order":
            return self._decline_order(arg)



        # ✅ normal tool routing
        if tool not in self.tools:
            return "Unknown tool."

        raw = self.tools[tool].run(arg)

        if isinstance(raw, list):
            raw = "\n\n".join(raw)
        else:
            raw = str(raw)

        #  Extract ingredients from raw context (new extraction)
        ingredients_list = self.extract_ingredients_from_text(raw)

        #  If the tool was 'ingredients', store ingredients for this user
        
        if ingredients_list:
            self.pending_ingredients["local-user"] = ingredients_list

            formatted = "\n".join([f"- {i}" for i in ingredients_list])

            return (
                f"Here are the ingredients I found:\n{formatted}\n\n"
                "Would you like me to order ALL these ingredients for you?"
            )


        # ✅ Otherwise run your grounding prompt
        reflect_prompt = (
            "Use the following context to answer the user's question.\n"
            "If the answer is not present in the context, reply: "
            "\"I don't know based on the available data.\"\n\n"
            f"Context:\n{raw}\n\n"
            f"Question: {arg}\n"
            "Answer based on the context above:"
        )

        out = self.client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT"),
            messages=[{"role": "user", "content": reflect_prompt}],
        )

        answer_text = out.choices[0].message.content

        return answer_text
  
        
      

    def handle_message(self, user, msg):
        
        # ✅ Welcome-back personalization
        history = self.order_manager.get_order_history("local-user")
        if history and msg.lower() in ["hi", "hello", "hey"] :  #
            last_order = history[-1]
            return (
                "Welcome back! 👋\n"
                "Based on your previous order, you may like these items:\n"
                "- " + "\n- ".join(last_order[:3]) + "\n\n"
                "How can I help you today?"
            )

        action = self.decide(msg)
        return self.run(action)
