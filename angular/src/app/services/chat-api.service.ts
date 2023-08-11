import { Injectable } from '@angular/core';
import axios from 'axios';
import { environment } from '../environments/environment';

@Injectable({
  providedIn: 'root',
})
export class ChatApiService {
  private API_URL = environment.API_URL;

  constructor() {}
  getChatResponse(message: string, id?: string) {
    return axios.post(`${this.API_URL}/chatbot`, {
      chat_id: id,
      message: message,
    });
  }
}
