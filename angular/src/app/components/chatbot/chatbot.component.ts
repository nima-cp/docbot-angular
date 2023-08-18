import { Component, OnInit } from '@angular/core';
import axios from 'axios';
import { ChatApiService } from 'src/app/services/chat-api.service';
import { v4 as uuidv4 } from 'uuid';
import { environment } from '../../environments/environment';

interface Messages {
  id?: string;
  from?: 'user' | 'bot';
  message?: string;
  date?: Date;
}
interface Chats {
  chat_id: number;
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
  private API_URL = environment.API_URL;

  chats?: Chats[];
  new_message: string = '';
  chat_history: [] = [];
  prompt: Prompt = {
    completion_tokens: 0,
    prompt_tokens: 0,
    total_tokens: 0,
    total_cost: 0,
  };
  selected_chat: number = 1;

  constructor(private ChatApiService: ChatApiService) {}

  ngOnInit() {
    this.ChatApiService.loadChatHistory().then((response) => {
      this.chats = response.data.chats;
      // this.selected_chat = this.chats[this.selected_chat].chat_id;
    });

    // this.chat.messages?.push({
    //   id: uuidv4(),
    //   from: 'bot',
    //   message: 'Benvenuto in DocBot!',
    //   date: new Date(),
    // });
    // this.chat.messages?.push({
    //   id: uuidv4(),
    //   from: 'bot',
    //   message: 'Come posso aiutarti?',
    //   date: new Date(),
    // });
  }

  send_message() {
    if (this.new_message.trim() === '') return;

    this.ChatApiService.getChatResponse(this.new_message)
      .then((response) => {
        // this.chat_history = response.data.chat_history;

        this.scrollToBottom();

        // this.chat.messages = response.data.chat_history;

        // this.prompt = response.data.response.prompt;
        // this.chat.chat_id = response.data.chat_id;
        //
        // console.log('chat_history', this.chat_history);
        console.log(response);
      })
      .catch((error) => {
        console.log(error);
      });

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
    axios.get(`${this.API_URL}/load_chats`).then((response) => {
      // const new_chat_id = response.data.chat_id;
      // console.log(response.data.chats);
      console.log(this.chats);

      // this.chat.messages = [];
    });
  }

  change_chat(chat_id: number) {
    this.selected_chat = chat_id - 1;
    console.log(chat_id);
  }
}
