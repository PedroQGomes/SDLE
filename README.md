# MIEI - 4ºAno - Sistemas Distribuídos em Larga Escala

O trabalho pratico proposto consiste no desenvolvimento um de serviço de timeline descentralizada, tento como inspiração o twitter,instagram etc. Os utilizadores do serviço tem uma identidade e publicam mensagens para a sua timeline local sendo depois reencaminhada para os utilizadores que o estão a seguir. Deste modo foi usada uma distributed hash table (DHT), `Kademlia`, para construir a rede peer to peer.

Algumas das funcionalidades implementadas no nosso sistema são as seguintes

* Difusão controlada de mensagens
* Efemeridade das mensagens 
* Ordenação causal das mensagens 
* Tempo físico das mensagens



# Testes

Para testar a rede é necessário correr o seguinte comando em que os dois primeiros portes tem de ser únicos e o Bootstrap port serve para inserir o nodo na rede peer to peer e deste modo tem de ser o port de um nodo já existente. No caso de ser o primeiro deve ser zero.

```
sudo python peer.py <DHT port> <Tcp Port> <Bootstrap Port>
```
