import { Component, OnInit } from '@angular/core';
import { ChatApiService } from 'src/app/services/chat-api.service';
import { v4 as uuidv4 } from 'uuid';

interface Message {
  id?: string;
  message?: string;
}

interface Messages {
  bot: Message[];
  user: Message[];
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
  messages: Messages = {
    bot: [],
    user: [],
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
    this.messages.bot.push({ id: uuidv4(), message: 'Benvenuto in DocBot!' });
    this.messages.bot.push({ id: uuidv4(), message: 'Come posso aiutarti?' });
    console.log('conversation', this.messages);
  }

  send_message() {
    if (this.new_message.trim() === '') return;

    this.messages.user.push({ id: uuidv4(), message: this.new_message });

    this.ChatApiService.getChatResponse(this.new_message)
      .then((response) => {
        this.chat_history = response.data.chat_history;
        this.answer = response.data.response.result.answer;
        this.messages.bot.push({
          id: uuidv4(),
          message: this.answer,
        });

        this.prompt = response.data.response.prompt;

        console.log('conversation', this.messages);
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
    console.log('new chat!');
  }
}
