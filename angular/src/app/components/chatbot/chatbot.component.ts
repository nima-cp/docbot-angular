import { Component, OnInit } from '@angular/core';
import { ChatApiService } from 'src/app/services/chat-api.service';

@Component({
  selector: 'app-chatbot',
  templateUrl: './chatbot.component.html',
  styleUrls: ['./chatbot.component.css'],
})
export class ChatbotComponent implements OnInit {
  messages: string[] = [];
  newMessage: string = '';

  constructor(private ChatApiService: ChatApiService) {}

  ngOnInit() {
    this.messages.push('Welcome to the DocBot!');
  }

  sendMessage() {
    if (this.newMessage.trim() === '') return;

    this.messages.push('User: ' + this.newMessage);
    console.log(this.messages);

    this.ChatApiService.getChatResponse(this.newMessage)
      .then((response) => {
        this.messages.push('Chatbot: ' + response.data.result.answer);
        console.log(response);
      })
      .catch((error) => {
        console.log(error);
      });

    this.newMessage = '';
  }
}
