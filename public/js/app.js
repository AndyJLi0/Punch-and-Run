let auth0 = null;

const initializeAuth0 = async () => {
  auth0 = await createAuth0Client({
    domain: 'dev-p31m3pajoolid65y.us.auth0.com', // Replace with your Auth0 domain
    client_id: 'sEvdw9OjmdetZsNJyx7vbiQ7CYNnjGE2' // Replace with your Auth0 client ID
  });

  // Handle the authentication state of the page
  updateUI();
};

const updateUI = async () => {
  const isAuthenticated = await auth0.isAuthenticated();

  document.getElementById('btn-login').disabled = isAuthenticated;
  document.getElementById('btn-logout').disabled = !isAuthenticated;

  // ... (display user profile or handle logged-out state)
};

const login = async () => {
  await auth0.loginWithRedirect({
    redirect_uri: 'http://localhost:3000/index.html'
  });
};

const logout = () => {
  auth0.logout({
    returnTo: 'http://localhost:3000/index.html'
  });
};


window.onload = async () => {
  initializeAuth0();

  // Check if the user is returning from Auth0
  const isAuthenticated = await auth0.isAuthenticated();
  if (!isAuthenticated) {
    // Check the code and state parameters
    const query = window.location.search;
    if (query.includes("code=") && query.includes("state=")) {
      // Process the login state
      await auth0.handleRedirectCallback();
      
      // Use replaceState to remove the code and state parameters
      window.history.replaceState({}, document.title, "/");
    }
  }

  updateUI();
};
