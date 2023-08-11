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
interface Chat {
  sessionId: number;
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

  chat: Chat = {
    sessionId: 1,
    messages: [],
  };
  new_message: string = '';
  chat_history: [] = [];
  answer?: string;
  prompt: Prompt = {
    completion_tokens: 0,
    prompt_tokens: 0,
    total_tokens: 0,
    total_cost: 0,
  };

  constructor(private ChatApiService: ChatApiService) {}

  ngOnInit() {
    this.chat.messages?.push({
      id: uuidv4(),
      from: 'bot',
      message: 'Benvenuto in DocBot!',
      date: new Date(),
    });
    this.chat.messages?.push({
      id: uuidv4(),
      from: 'bot',
      message: 'Come posso aiutarti?',
      date: new Date(),
    });
  }

  // Sort messages by date
  getSortedMessages() {
    return this.chat.messages?.sort((a, b) => {
      const ad = a as { date: Date };
      const bd = b as { date: Date };
      return ad.date.getTime() - bd.date.getTime();
    });
  }

  send_message() {
    if (this.new_message.trim() === '') return;

    this.chat.messages?.push({
      id: uuidv4(),
      from: 'user',
      message: this.new_message,
      date: new Date(),
    });

    this.ChatApiService.getChatResponse(this.new_message)
      .then((response) => {
        this.chat_history = response.data.chat_history;
        this.answer = response.data.response.result.answer;

        this.chat.messages?.push({
          id: uuidv4(),
          from: 'bot',
          message: this.answer,
          date: new Date(),
        });

        this.prompt = response.data.response.prompt;

        console.log('conversation', this.chat?.messages);
        console.log('chat_history', this.chat_history);
        console.log('prompt', this.prompt);
        console.log(response);
      })
      .catch((error) => {
        console.log(error);
      });

    this.new_message = '';
  }

  restartDB() {
    console.log('DB Restarted!');
    // this.ChatApiService.restartDB(() => {
    // });
  }
  new_chat() {
    axios.get(`${this.API_URL}/new_chat`, {}).then((response) => {
      const new_chat_id = response.data;
      console.log(response);
      console.log(response.headers);
      console.log(response.headers['chat_id']);
      this.chat.messages = [];
    });
  }
}
