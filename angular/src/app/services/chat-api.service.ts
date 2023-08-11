import { Injectable } from '@angular/core';
import axios from 'axios';
import { environment } from '../environments/environment';

@Injectable({
  providedIn: 'root',
})
export class ChatApiService {
  private API_URL = environment.API_URL;

  constructor() {}
  getChatResponse(message: any) {
    return axios.post(`${this.API_URL}/chatbot`, {
      session_id: 1,
      message: message,
    });
  }
}
