# microsoftfoundryportal-multiagents
Project created to showcase how the query from user is directed to different agents like support, sales based on the intent of the query or direct to generic answer given by LLM Model if it is not related to sales or support.

<img width="1387" height="432" alt="image" src="https://github.com/user-attachments/assets/c2bf592d-06d0-42eb-8042-cd19cae621fb" />
In ai.azure.com Microsoft Foundry Portal :
3 Agents are created :<img width="3802" height="1260" alt="image" src="https://github.com/user-attachments/assets/71f271ac-13d3-4206-9501-1ea714bd05d2" />
In Browser :
    <img width="3735" height="2147" alt="image" src="https://github.com/user-attachments/assets/ff7595b7-ced0-4971-8f3c-769bf4e4aea2" />
1. Get /agent/deployment
     <img width="512" height="115" alt="image" src="https://github.com/user-attachments/assets/7d59206a-dd41-4312-9c63-208972c8cd57" />
     <img width="1582" height="985" alt="image" src="https://github.com/user-attachments/assets/c90b8c32-4ff9-4303-8a68-d946d0d15ab3" />
2. POST /agent/query
      a. Support Agent query
       In Browser
           <img width="310" height="170" alt="image" src="https://github.com/user-attachments/assets/d7f95787-6a05-4021-b00f-64060582e1ef" />           
       In VS Code Terminal :
           <img width="537" height="170" alt="image" src="https://github.com/user-attachments/assets/58ddb4a3-0e8a-4358-8c2b-7da50331b9f6" />
           <img width="1560" height="930" alt="image" src="https://github.com/user-attachments/assets/5d425cd2-f438-4924-a42d-3a1f2755586e" />           
        In Response from Support Agent :
           <img width="1585" height="745" alt="image" src="https://github.com/user-attachments/assets/0d759e5c-27fc-434e-842c-466f328a1fda" />

     b. Sales Agent query :
       In Browser
           <img width="425" height="180" alt="image" src="https://github.com/user-attachments/assets/6839b021-e410-4220-a687-7e398b85784d" />
       In VS Code Terminal :
           <img width="480" height="87" alt="image" src="https://github.com/user-attachments/assets/52ef43da-9233-49cc-a29b-b2313e41734e" />
       In Response from Sales Agent :
           <img width="1560" height="955" alt="image" src="https://github.com/user-attachments/assets/2c3a17e9-88bb-4ac3-93f6-04849b33b886" />

    c. General query :
       In Browser
           <img width="430" height="172" alt="image" src="https://github.com/user-attachments/assets/300ce50d-0d03-4544-93ca-2a92b31942f6" />
       In VS Code Terminal :
           <img width="485" height="80" alt="image" src="https://github.com/user-attachments/assets/cc5fe595-af3a-4146-9619-7daef2ecd2e4" />
       In Response routed to General Assistant which fetch result from LLM  :
           <img width="1557" height="967" alt="image" src="https://github.com/user-attachments/assets/db8e86f1-5b99-4575-822d-8a9cce2d2f2a" />

3. POST /agent/cleanup
     In Browser
         <img width="585" height="925" alt="image" src="https://github.com/user-attachments/assets/7bf14cb0-1e9f-4e71-a67c-3f564d36cdf6" />
      In VS Code Terminal :
         <img width="720" height="132" alt="image" src="https://github.com/user-attachments/assets/97ba9a38-b928-41a4-9913-6fba642f75d6" />
     In Azure Foundry Portal <ai.azure.com> :
         <img width="550" height="285" alt="image" src="https://github.com/user-attachments/assets/1266e37b-f21c-4a3a-9ec1-9000b1e41690" />


