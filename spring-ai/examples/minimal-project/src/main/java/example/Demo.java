package example;
import org.springframework.ai.chat.client.ChatClient;
class Demo {
  ChatClient client;
  String answer(String question, String conversationId) {
    return client.prompt().user(question).call().content();
  }
}
