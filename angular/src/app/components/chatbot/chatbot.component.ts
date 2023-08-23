import { Component, OnInit } from '@angular/core';
import { ChatApiService } from 'src/app/services/chat-api.service';

interface Message {
  id?: string;
  from?: 'user' | 'bot';
  message?: string;
  date?: Date;
}

interface Chat {
  chat_id?: number;
  title?: string;
  messages?: Message[];
}

interface Tokens {
  completion_tokens?: number;
  prompt_tokens?: number;
  total_tokens?: number;
  total_cost?: number;
}

@Component({
  selector: 'app-chatbot',
  templateUrl: './chatbot.component.html',
  styleUrls: ['./chatbot.component.css'],
})
export class ChatbotComponent implements OnInit {
  chats: Chat[] = [];
  new_message: string = '';
  tokens: Tokens = {
    completion_tokens: 0,
    prompt_tokens: 0,
    total_tokens: 0,
    total_cost: 0,
  };
  selected_chat?: Chat = {};
  open_new_chat: boolean = false;
  errorMessage?: string = '';

  constructor(private ChatApiService: ChatApiService) {}

  async ngOnInit() {
    await this.load_chat_history();
    this.selected_chat = this.get_selected_chat(this.selected_chat?.chat_id);
    if (!this.selected_chat) this.new_chat();
  }

  private async load_chat_history() {
    try {
      const response = await this.ChatApiService.loadChatHistory();
      this.chats = response.data.chats;

      if (!this.selected_chat?.chat_id) this.selected_chat = this.chats[0];
    } catch (error) {
      console.error('An error occurred while loading chat history:', error);
      this.errorMessage =
        'An error occurred while loading chat history. Please try again.';
    }
  }

  async send_message() {
    this.errorMessage = '';
    if (this.new_message.trim() === '') return;
    this.selected_chat!.messages?.push({
      from: 'user',
      message: this.new_message,
    });
    this.scrollToBottom();
    const question = this.new_message;
    this.new_message = '';

    try {
      const response = await this.ChatApiService.getChatResponse(
        question,
        this.open_new_chat ? undefined : this.selected_chat?.chat_id
      );
      console.log('response', response);

      this.open_new_chat = false;
      this.selected_chat!.chat_id = response.data.chat_id;
      this.tokens = response.data.tokens;

      await this.load_chat_history();
      this.selected_chat = this.get_selected_chat(this.selected_chat!.chat_id);

      this.scrollToBottom();
    } catch (error: any) {
      if (error.response) {
        // The request was made and the server responded with a status code
        // that falls out of the range of 2xx
        console.log('Error Type 1: Server Response Error');
        console.log('Error Data:', error.response.data);
        console.log('Status Code:', error.response.status);
        console.log('Response Headers:', error.response.headers);
        this.errorMessage =
          'Server responded with an error: ' + error.response.data.error;
      } else if (error.request) {
        // The request was made but no response was received
        // `error.request` is an instance of XMLHttpRequest in the browser and an instance of
        // http.ClientRequest in node.js
        console.log('Error Type 2: No Response Received');
        console.log('Request:', error.request);
        this.errorMessage = 'No response received from the server.';
      } else {
        // Something happened in setting up the request that triggered an Error
        console.log('Error Type 3: Request Setup Error');
        console.log('Error Message:', error.message);
        this.errorMessage = 'An error occurred while setting up the request.';
      }
      console.log('Request Config:', error.config);
    }
  }

  scrollToBottom() {
    const chatContainer = document.getElementById('messages_container');
    if (chatContainer) chatContainer.scrollTop = chatContainer.scrollHeight;
  }

  restartDB() {
    console.log('DB Restarted!');
    // this.ChatApiService.restartDB()
  }

  new_chat() {
    this.open_new_chat = true;

    if (!this.selected_chat) {
      this.selected_chat = {};
    }

    this.selected_chat!.messages = [
      {
        from: 'bot',
        message: 'Ciao, come posso aiutarti?',
      },
    ];
  }

  async change_chat(clicked_chat_id?: number) {
    this.open_new_chat = false;
    await this.load_chat_history();
    this.selected_chat!.chat_id = clicked_chat_id;
    this.selected_chat = this.get_selected_chat(this.selected_chat?.chat_id);
    console.log('Chat changed to:', this.selected_chat);
    this.scrollToBottom();
  }

  get_selected_chat(chatId?: number): Chat | undefined {
    return this.chats.find((chat) => chat.chat_id === chatId);
  }

  sort_chats_by_latest_messages(chats: Chat[]): Chat[] {
    return chats.sort((a, b) => {
      const latestMessageA = a.messages?.length
        ? new Date(a.messages.at(-1)?.date ?? '')
        : undefined;
      const latestMessageB = b.messages?.length
        ? new Date(b.messages.at(-1)?.date ?? '')
        : undefined;

      if (latestMessageA && latestMessageB)
        return latestMessageB.getTime() - latestMessageA.getTime();
      else if (latestMessageA) return -1; // A has a message, but B doesn't
      else if (latestMessageB) return 1; // B has a message, but A doesn't

      return 0; // Both A and B don't have messages
    });
  }
}
