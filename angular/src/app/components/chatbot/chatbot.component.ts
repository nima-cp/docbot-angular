import { Component, OnInit } from '@angular/core';
import { ChatApiService } from 'src/app/services/chat-api.service';

interface Messages {
  id?: string;
  from?: 'user' | 'bot';
  message?: string;
  date?: Date;
}
interface Chats {
  chat_id?: number;
  title?: string;
  messages?: Messages[];
}

interface Prompt {
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
  chats: Chats[] = [];
  new_message: string = '';
  chat_history: [] = [];
  prompt: Prompt = {
    completion_tokens: 0,
    prompt_tokens: 0,
    total_tokens: 0,
    total_cost: 0,
  };
  selected_chat?: Chats = {};
  open_new_chat: boolean = false;

  constructor(private ChatApiService: ChatApiService) {}

  async ngOnInit() {
    await this.load_chat_history();
    this.selected_chat = this.get_selected_chat(this.selected_chat?.chat_id);

    if (!this.selected_chat?.messages) {
      console.error('Selected chat does not exist.');
      // this.new_chat();
    }
  }

  private async load_chat_history() {
    await this.ChatApiService.loadChatHistory().then(
      (response) => (this.chats = response.data.chats)
    );

    if (!this.selected_chat?.chat_id)
      this.selected_chat!.chat_id = this.chats[0].chat_id;
  }

  async send_message() {
    if (this.new_message.trim() === '') return;

    await this.ChatApiService.getChatResponse(
      this.new_message,
      this.open_new_chat ? undefined : this.selected_chat?.chat_id
    )
      .then((response) => {
        this.open_new_chat = false;
        console.log(response);
        this.selected_chat!.chat_id = response.data.chat_id;
      })
      .catch((error) => {
        console.log(error);
      });

    await this.load_chat_history();
    this.selected_chat = this.get_selected_chat(this.selected_chat!.chat_id);

    this.scrollToBottom();
    this.new_message = '';
  }

  scrollToBottom() {
    let chatContainer = document.getElementById('messages_container');
    chatContainer!.scrollTop = chatContainer!.scrollHeight;
  }

  restartDB() {
    console.log('DB Restarted!');
    // this.ChatApiService.restartDB()
  }

  new_chat() {
    this.open_new_chat = true;
    this.selected_chat!.messages = [
      {
        from: 'bot',
        message: 'Ciao, come posso aiutarti?',
        // date: new Date(),
      },
    ];
  }

  async change_chat(chat_id_clicked?: number) {
    await this.load_chat_history();
    this.selected_chat!.chat_id = chat_id_clicked;
    this.selected_chat = this.get_selected_chat(this.selected_chat?.chat_id);
    console.log('Chat changed to:', this.selected_chat);
    this.scrollToBottom();
  }

  get_selected_chat(chat_ID?: number): Chats | undefined {
    if (this.selected_chat) {
      return this.chats.find((chat) => chat.chat_id === chat_ID);
    }
    return undefined;
  }
}
