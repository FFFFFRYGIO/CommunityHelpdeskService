describe('template spec', () => {

    beforeEach(() => {
        cy.register_user('testuser', 'ph1shstix!');
        cy.login_user('testuser', 'ph1shstix!');
    });

    it('Create Article Test', () => {
        cy.visit('http://127.0.0.1:8000/user_app/create_article/');

        cy.get('#id_title').type('Test Article Title');
        cy.get('#id_tags').type('tag1, tag2, tagtest');

        cy.get('#id_form-0-title').type('Test Step 1 title');
        cy.get('#id_form-0-description1').type('Test Step 1 description1');
        cy.get('#id_form-0-description2').type('Test Step 1 description2');

        cy.get('#add-step-button').click();

        cy.get('#id_form-1-title').type('Test Step 2 title');
        cy.get('#id_form-1-description1').type('Test Step 2 description1');
        cy.get('#id_form-1-description2').type('Test Step 2 description2');

        cy.get('button[type="submit"]').click();

        cy.visit('http://127.0.0.1:8000/user_app/user_panel/');

        cy.get('.card-body').should('contain', 'Test Article Title');
        cy.get('.card-body').should('contain', 'testuser');
        cy.get('.card-body').should('contain', 'Steps: 2');
        cy.get('.card-body').should('contain', '\n' +
            '                    Tags: \n' +
            '                    #tag1 \n' +
            '                \n' +
            '                    #tagtest \n' +
            '                \n' +
            '                    #tag2\n' +
            '                \n' +
            '                ');

    });

    afterEach(() => {
        cy.visit('http://127.0.0.1:8000/registration/logout');
        cy.cleanup_user('testuser');
    });

});
