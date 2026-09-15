// insercion.c
#include "isam_core.h"

void insertar_registro(Record nuevo_registro) {
    // 1. Llamada a la función de búsqueda (con mock data)
    DataPage* pagina = buscar_pagina(nuevo_registro.search_key);    
    
    
    if (pagina == NULL) {
        // Manejar error
        printf("No se encontro la pagina");
        return;
    }
    
    // 2. Lógica de inserción y Overflow
    int key=nuevo_registro.search_key;
    if (pagina->current_count < MAX_RECORDS) {        
        if(pagina->current_count==0){
            pagina->records[pagina->current_count]=nuevo_registro;
            pagina->current_count+=1;
        }else{
            for(int i=0;i<pagina->current_count;i++){
                
                if(key<pagina->records[i].search_key){
                
                    for(int j=pagina->current_count;j!=i;j--){
                        pagina->records[j]=pagina->records[j-1];
                    }
                    pagina->records[i]=nuevo_registro;
                    pagina->current_count+=1;
                    return;

                }else{
                    continue;
                }
            }
            pagina->records[pagina->current_count]=nuevo_registro;
            pagina->current_count+=1;           
            
        }      
        
    } else {
        
        DataPage **p;
        p=&pagina;
        while((*p)->overflow && (*p)->overflow->current_count==MAX_RECORDS){
            p=&((*p)->overflow);
        }        

        if((*p)->overflow==NULL && (*p)->current_count==MAX_RECORDS){            
            DataPage *nuevaPagina=palloc(sizeof(DataPage));
            nuevaPagina->current_count=0;            
            (*p)->overflow=nuevaPagina;
            nuevaPagina->overflow=NULL;
            p=&((*p)->overflow);
        }
        else if((*p)->overflow != NULL){
             p=&((*p)->overflow);
        }
        
        if((*p)->current_count==0){
            (*p)->records[(*p)->current_count]=nuevo_registro;
            (*p)->current_count+=1;
        }else{

            for(int i=0;i<(*p)->current_count;i++){
                
                if(key<(*p)->records[i].search_key){
                
                    for(int j=(*p)->current_count;j!=i;j--){
                        (*p)->records[j]=(*p)->records[j-1];
                    }
                    (*p)->records[i]=nuevo_registro;
                    (*p)->current_count+=1;
                    return;

                }else{
                    continue;
                }
            }
            (*p)->records[(*p)->current_count]=nuevo_registro;
            (*p)->current_count+=1;
            
            
        }   
        


    }
}
