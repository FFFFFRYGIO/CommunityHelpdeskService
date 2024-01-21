describe('template spec', () => {

    beforeEach(() => {
        cy.fixture('user').then(user => {
            cy.register_user(user.username, user.password);
            cy.login_user(user.username, user.password);
        });
    });

    it('Home Test', () => {

        cy.visit('http://127.0.0.1:8000/user_app/home/');
        cy.get('button').contains('Search articles').click();
        cy.location().should((loc) => {
            expect(loc.href).to.eq(
                'http://127.0.0.1:8000/user_app/search/?'
            );
        });

        cy.visit('http://127.0.0.1:8000/user_app/home/');
        cy.get('button').contains('Create new article').click();
        cy.location().should((loc) => {
            expect(loc.href).to.eq(
                'http://127.0.0.1:8000/user_app/create_article/?'
            );
        });

        cy.visit('http://127.0.0.1:8000/user_app/home/');
        cy.get('button').contains('Go to user panel').click();
        cy.location().should((loc) => {
            expect(loc.href).to.eq(
                'http://127.0.0.1:8000/user_app/user_panel/?'
            );
        });

    });

    afterEach(() => {
        cy.visit('http://127.0.0.1:8000/registration/logout');
        cy.fixture('user').then(user => {
            cy.cleanup_user(user.username);
        });
    });

});
