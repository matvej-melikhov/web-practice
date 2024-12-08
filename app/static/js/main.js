function confirmDelete(event) {
    const button = event.target;
    const habitId = button.getAttribute('data-habit-id');
    console.log("Deleting habit with ID:", habitId);

    // Отправляем AJAX-запрос на сервер
    fetch(`/habit/${habitId}/delete`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': '{{ csrf_token() }}'  // если используешь CSRF защиту
        },
        body: JSON.stringify({ habit_id: habitId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            const habitElement = document.getElementById('habit-' + habitId);
            if (habitElement) {
                habitElement.remove();
                console.log("Habit deleted successfully.");
            } else {
                console.log("Error: Habit element not found in DOM.");
            }
        } else {
            console.log("Error deleting habit.");
        }
    })
    .catch(error => {
        console.log("Error deleting habit:", error);
    });
}

