import { Injectable } from '@angular/core';
import axios from 'axios';

@Injectable({
  providedIn: 'root',
})
export class ChatApiService {
  constructor() {}
  getChatResponse(message: any) {
    return axios.post('http://127.0.0.1:8080/chatbot', {
      message: message,
    });
  }
}
