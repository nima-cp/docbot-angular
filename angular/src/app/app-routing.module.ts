import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { ChatbotComponent } from './chatbot/chatbot.component';
import { Chat2Component } from './chat2/chat2.component';

const routes: Routes = [{ path: '', component: Chat2Component }];
@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule],
})
export class AppRoutingModule {}
