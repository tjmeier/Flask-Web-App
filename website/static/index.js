function deleteNote(noteID) {
    fetch('/delete-note', {
        method: 'POST',
        body: JSON.stringify({noteId: noteID}),
    }).then((_res) => {
        window.location.href = "/" //reloads the home page
    }); 

}

