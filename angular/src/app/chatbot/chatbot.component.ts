import { Component } from '@angular/core';
import 'deep-chat';

@Component({
  selector: 'app-root',
  templateUrl: './chatbot.component.html',
  styleUrls: ['./chatbot.component.css'],
})
export class ChatbotComponent {
  initialMessages = [
    { role: 'user', text: 'Hey, how are you today?' },
    { role: 'ai', text: 'I am doing very well!' },
    { role: 'ai', text: 'How can I help you?' },
  ];
}
