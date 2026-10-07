const miPromesa = new Promise((resolve, reject) => {
  // Operación asíncrona
  const exito = true;
  
  if (exito) {
    resolve("¡Operación exitosa!");
  } else {
    reject("Algo salió mal");
  }
});

// Usar la promesa
miPromesa
  .then(resultado => console.log(resultado))
  .catch(error => console.error(error));