document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          <div class="participants">
            <h5>Participants</h5>
          </div>
        `;

        // Create participants section with proper escaping
        const participantsDiv = activityCard.querySelector('.participants');
        if (details.participants && details.participants.length) {
          const ul = document.createElement('ul');
          ul.className = 'participant-list';
          
          details.participants.forEach(email => {
            const li = document.createElement('li');
            li.setAttribute('data-activity', name);
            li.setAttribute('data-email', email);
            
            const span = document.createElement('span');
            span.className = 'participant-name';
            span.textContent = email; // Use textContent to prevent XSS
            
            const btn = document.createElement('button');
            btn.className = 'delete-participant';
            btn.title = 'Unregister';
            btn.setAttribute('aria-label', `Unregister ${email}`);
            btn.textContent = '🗑️';
            
            // Attach event listener directly without setTimeout
            btn.addEventListener('click', async function(e) {
              e.preventDefault();
              const activityName = li.getAttribute('data-activity');
              const participantEmail = li.getAttribute('data-email');
              if (confirm(`Unregister ${participantEmail} from ${activityName}?`)) {
                try {
                  const response = await fetch(`/activities/${encodeURIComponent(activityName)}/unregister?email=${encodeURIComponent(participantEmail)}`, { method: 'POST' });
                  if (response.ok) {
                    fetchActivities(); // Refresh activities list after unregister
                  } else {
                    alert('Failed to unregister participant.');
                  }
                } catch (err) {
                  alert('Error occurred while unregistering.');
                }
              }
            });
            
            li.appendChild(span);
            li.appendChild(btn);
            ul.appendChild(li);
          });
          
          participantsDiv.appendChild(ul);
        } else {
          const p = document.createElement('p');
          p.className = 'no-participants';
          p.textContent = 'No participants yet';
          participantsDiv.appendChild(p);
        }

        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
        fetchActivities(); // Refresh activities list after signup
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchActivities();
});
