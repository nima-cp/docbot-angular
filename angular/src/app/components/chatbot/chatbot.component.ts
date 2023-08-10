import { Component, OnInit } from '@angular/core';
import { ChatApiService } from 'src/app/services/chat-api.service';

interface Messages {
  bot: string[];
  user: string[];
}

interface Prompt {
  completion_tokens?: number;
  prompt_tokens?: number;
  total_cost?: number;
  total_tokens?: number;
}

@Component({
  selector: 'app-chatbot',
  templateUrl: './chatbot.component.html',
  styleUrls: ['./chatbot.component.css'],
})
export class ChatbotComponent implements OnInit {
  messages: Messages = { bot: [], user: [] };
  new_message: string = '';
  chat_history: [] = [];
  answer: string = '';
  prompt: Prompt = {};

  constructor(private ChatApiService: ChatApiService) {}

  ngOnInit() {
    this.messages.bot.push('Benvenuto in DocBot!');
    this.messages.bot.push('Come posso aiutarti?');
  }

  send_message() {
    if (this.new_message.trim() === '') return;

    this.messages.user.push(this.new_message);

    this.ChatApiService.getChatResponse(this.new_message)
      .then((response) => {
        this.chat_history = response.data.chat_history;
        this.answer = response.data.response.result.answer;
        this.messages.bot.push(this.answer);

        this.prompt = response.data.response.prompt;

        console.log(response);
      })
      .catch((error) => {
        console.log(error);
      });

    this.new_message = '';

    console.log('conversation', this.messages);
    console.log('chat_history', this.chat_history);
    console.log('prompt', this.prompt);
  }
}
