import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-chatbot',
  templateUrl: './chatbot.component.html',
  styleUrls: ['./chatbot.component.css'],
})
export class ChatbotComponent implements OnInit {
  messages: string[] = [];
  newMessage: string = '';

  constructor(private http: HttpClient) {}

  ngOnInit() {
    this.messages.push('Welcome to the DocBot!');
  }

  sendMessage() {
    if (this.newMessage.trim() === '') return;

    this.messages.push('User: ' + this.newMessage);
    console.log(this.messages);

    this.http
      .post<any>('http://127.0.0.1:8080/chatbot', { message: this.newMessage })
      .subscribe((response) => {
        this.messages.push('Chatbot: ' + response.response);
        console.log(response);
      });

    this.newMessage = '';
  }
}
